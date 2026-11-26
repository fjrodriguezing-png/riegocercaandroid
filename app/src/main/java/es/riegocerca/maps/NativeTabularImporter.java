package es.riegocerca.maps;

import android.content.Context;
import android.database.Cursor;
import android.net.Uri;
import android.provider.OpenableColumns;
import org.json.JSONArray;
import org.json.JSONObject;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;
import javax.xml.parsers.DocumentBuilderFactory;
import java.io.*;
import java.text.Normalizer;
import java.util.*;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

public class NativeTabularImporter {
    private final Context context;
    public NativeTabularImporter(Context context) { this.context = context; }

    public JSONArray read(Uri uri) throws Exception {
        String name = fileName(uri).toLowerCase(Locale.ROOT);
        if (name.endsWith(".csv")) return csv(uri);
        if (name.endsWith(".xlsx")) return xlsx(uri);
        throw new Exception("Formato no compatible. Selecciona un archivo .xlsx o .csv");
    }

    private String fileName(Uri uri) {
        String name = "";
        try (Cursor cursor = context.getContentResolver().query(uri, null, null, null, null)) {
            if (cursor != null && cursor.moveToFirst()) {
                int index = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME);
                if (index >= 0) name = cursor.getString(index);
            }
        } catch (Exception ignored) {}
        return name == null ? "" : name;
    }

    private JSONArray csv(Uri uri) throws Exception {
        try (BufferedReader br = new BufferedReader(new InputStreamReader(context.getContentResolver().openInputStream(uri), "UTF-8"))) {
            List<String[]> lines = new ArrayList<>();
            String line;
            char sep = ';';
            while ((line = br.readLine()) != null) {
                if (lines.isEmpty()) sep = line.contains(";") ? ';' : ',';
                lines.add(splitCsv(line, sep));
            }
            return rowsToJson(lines);
        }
    }

    private String[] splitCsv(String line, char sep) {
        List<String> values = new ArrayList<>();
        StringBuilder value = new StringBuilder();
        boolean quoted = false;
        for (int i = 0; i < line.length(); i++) {
            char ch = line.charAt(i);
            if (ch == '"') {
                if (quoted && i + 1 < line.length() && line.charAt(i + 1) == '"') { value.append('"'); i++; }
                else quoted = !quoted;
            } else if (ch == sep && !quoted) { values.add(value.toString()); value.setLength(0); }
            else value.append(ch);
        }
        values.add(value.toString());
        return values.toArray(new String[0]);
    }

    private JSONArray xlsx(Uri uri) throws Exception {
        File temp = File.createTempFile("crnl_", ".xlsx", context.getCacheDir());
        try (InputStream in = context.getContentResolver().openInputStream(uri); OutputStream out = new FileOutputStream(temp)) {
            if (in == null) throw new Exception("No se pudo abrir el Excel");
            byte[] buffer = new byte[8192]; int n;
            while ((n = in.read(buffer)) > 0) out.write(buffer, 0, n);
        }

        Map<String, byte[]> entries = new HashMap<>();
        try (ZipInputStream zip = new ZipInputStream(new FileInputStream(temp))) {
            ZipEntry entry;
            while ((entry = zip.getNextEntry()) != null) {
                String name = entry.getName();
                if (name.equals("xl/sharedStrings.xml") || name.equals("xl/worksheets/sheet1.xml")) {
                    ByteArrayOutputStream data = new ByteArrayOutputStream();
                    byte[] buffer = new byte[4096]; int n;
                    while ((n = zip.read(buffer)) > 0) data.write(buffer, 0, n);
                    entries.put(name, data.toByteArray());
                }
            }
        } finally { temp.delete(); }

        List<String> shared = sharedStrings(entries.get("xl/sharedStrings.xml"));
        byte[] sheet = entries.get("xl/worksheets/sheet1.xml");
        if (sheet == null) throw new Exception("No se encontró la primera hoja del Excel");

        Document doc = DocumentBuilderFactory.newInstance().newDocumentBuilder().parse(new ByteArrayInputStream(sheet));
        NodeList xmlRows = doc.getElementsByTagName("row");
        List<String[]> lines = new ArrayList<>();
        for (int r = 0; r < xmlRows.getLength(); r++) {
            NodeList cells = ((Element) xmlRows.item(r)).getElementsByTagName("c");
            Map<Integer, String> values = new HashMap<>(); int max = -1;
            for (int c = 0; c < cells.getLength(); c++) {
                Element cell = (Element) cells.item(c);
                int index = columnIndex(cell.getAttribute("r"));
                String type = cell.getAttribute("t");
                String value = "";
                if ("inlineStr".equals(type)) {
                    NodeList text = cell.getElementsByTagName("t");
                    if (text.getLength() > 0) value = text.item(0).getTextContent();
                } else {
                    NodeList raw = cell.getElementsByTagName("v");
                    if (raw.getLength() > 0) value = raw.item(0).getTextContent();
                    if ("s".equals(type) && !value.isEmpty()) {
                        int si = Integer.parseInt(value);
                        value = si >= 0 && si < shared.size() ? shared.get(si) : "";
                    }
                }
                values.put(index, value); max = Math.max(max, index);
            }
            String[] row = new String[Math.max(0, max + 1)];
            for (int i = 0; i < row.length; i++) row[i] = values.getOrDefault(i, "");
            lines.add(row);
        }
        return rowsToJson(lines);
    }

    private JSONArray rowsToJson(List<String[]> lines) throws Exception {
        if (lines.isEmpty()) throw new Exception("El archivo está vacío");
        int headerRow = -1;
        for (int i = 0; i < Math.min(lines.size(), 20); i++) {
            Set<String> cols = new HashSet<>();
            for (String value : lines.get(i)) cols.add(norm(value));
            if (cols.contains("NOMBRE") && (cols.contains("X") || cols.contains("COORDENADAX")) && (cols.contains("Y") || cols.contains("COORDENADAY"))) { headerRow = i; break; }
        }
        if (headerRow < 0) throw new Exception("No encuentro las columnas NOMBRE, X y Y en las primeras 20 filas");
        String[] columns = lines.get(headerRow);
        JSONArray result = new JSONArray();
        for (int i = headerRow + 1; i < lines.size(); i++) {
            JSONObject row = makeRow(columns, lines.get(i));
            if (row != null) result.put(row);
        }
        if (result.length() == 0) throw new Exception("No se encontraron elementos válidos con NOMBRE, X e Y");
        return result;
    }

    private JSONObject makeRow(String[] columns, String[] values) throws Exception {
        String type = "", name = "", xs = "", ys = "";
        for (int i = 0; i < columns.length && i < values.length; i++) {
            String key = norm(columns[i]); String value = values[i] == null ? "" : values[i].trim();
            if (key.equals("TIPO")) type = value;
            else if (key.equals("NOMBRE")) name = value;
            else if (key.equals("X") || key.equals("COORDENADAX")) xs = value;
            else if (key.equals("Y") || key.equals("COORDENADAY")) ys = value;
        }
        if (name.isEmpty() || xs.isEmpty() || ys.isEmpty()) return null;
        return new JSONObject().put("type", type).put("name", name).put("x", number(xs)).put("y", number(ys));
    }

    private double number(String value) {
        String s = value.trim().replace(" ", "");
        if (s.contains(",") && s.contains(".")) {
            if (s.lastIndexOf(',') > s.lastIndexOf('.')) s = s.replace(".", "").replace(',', '.');
            else s = s.replace(",", "");
        } else if (s.contains(",")) s = s.replace(',', '.');
        return Double.parseDouble(s);
    }

    private String norm(String value) {
        return Normalizer.normalize(value == null ? "" : value, Normalizer.Form.NFD)
                .replaceAll("\\p{M}", "").replaceAll("[^A-Za-z0-9]", "").toUpperCase(Locale.ROOT);
    }

    private List<String> sharedStrings(byte[] bytes) throws Exception {
        List<String> values = new ArrayList<>();
        if (bytes == null) return values;
        Document doc = DocumentBuilderFactory.newInstance().newDocumentBuilder().parse(new ByteArrayInputStream(bytes));
        NodeList nodes = doc.getElementsByTagName("si");
        for (int i = 0; i < nodes.getLength(); i++) values.add(nodes.item(i).getTextContent());
        return values;
    }

    private int columnIndex(String reference) {
        int value = 0;
        for (int i = 0; i < reference.length() && Character.isLetter(reference.charAt(i)); i++)
            value = value * 26 + (Character.toUpperCase(reference.charAt(i)) - 'A' + 1);
        return value - 1;
    }
}
