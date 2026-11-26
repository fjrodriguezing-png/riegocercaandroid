package es.riegocerca.maps;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.GeolocationPermissions;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

import org.json.JSONArray;

public class MainActivity extends Activity {
    private WebView w;
    private ValueCallback<Uri[]> files;
    private GeolocationPermissions.Callback geo;
    private String origin;

    private static final int LOC = 7;
    private static final int FILE = 8;
    private static final int IMPORT_FILE = 9;

    @Override
    public void onCreate(Bundle b) {
        super.onCreate(b);

        w = new WebView(this);
        setContentView(w);

        WebSettings s = w.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setGeolocationEnabled(true);
        s.setAllowFileAccess(true);
        s.setAllowContentAccess(true);

        w.addJavascriptInterface(new MapsBridge(this), "AndroidMaps");
        w.addJavascriptInterface(new ImportBridge(this, IMPORT_FILE), "AndroidImport");

        w.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView v, String u) {
                try {
                    if (u.startsWith("https://wa.me/") || u.startsWith("https://earth.google.com/")) {
                        Intent i = new Intent(Intent.ACTION_VIEW, Uri.parse(u));
                        if (u.contains("earth.google.com")) i.setPackage("com.google.earth");
                        try {
                            startActivity(i);
                        } catch (Exception e) {
                            i.setPackage(null);
                            startActivity(i);
                        }
                        return true;
                    }
                } catch (Exception ignored) {
                }
                return false;
            }
        });

        w.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onGeolocationPermissionsShowPrompt(String o, GeolocationPermissions.Callback c) {
                origin = o;
                geo = c;
                if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
                        || checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED) {
                    c.invoke(o, true, true);
                    geo = null;
                } else {
                    requestPermissions(new String[]{
                            Manifest.permission.ACCESS_FINE_LOCATION,
                            Manifest.permission.ACCESS_COARSE_LOCATION
                    }, LOC);
                }
            }

            @Override
            public boolean onShowFileChooser(WebView v, ValueCallback<Uri[]> c, FileChooserParams p) {
                files = c;
                try {
                    startActivityForResult(p.createIntent(), FILE);
                    return true;
                } catch (Exception e) {
                    files = null;
                    return false;
                }
            }
        });

        w.loadUrl("file:///android_asset/index.html");
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if (requestCode == IMPORT_FILE) {
            if (resultCode != RESULT_OK || data == null || data.getData() == null) {
                w.evaluateJavascript("window.importError && window.importError('Importación cancelada')", null);
                return;
            }

            Uri uri = data.getData();
            try {
                getContentResolver().takePersistableUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION);
            } catch (Exception ignored) {
            }

            new Thread(() -> {
                try {
                    JSONArray result = new NativeTabularImporter(MainActivity.this).read(uri);
                    String json = result.toString();
                    runOnUiThread(() -> w.evaluateJavascript(
                            "window.receiveImportedRows && window.receiveImportedRows(" + json + ")", null));
                } catch (Exception e) {
                    final String message = e.getMessage() == null ? "No se pudo leer el archivo" : e.getMessage();
                    runOnUiThread(() -> {
                        Toast.makeText(MainActivity.this, message, Toast.LENGTH_LONG).show();
                        w.evaluateJavascript(
                                "window.importError && window.importError(" + org.json.JSONObject.quote(message) + ")", null);
                    });
                }
            }).start();
            return;
        }

        if (requestCode == FILE && files != null) {
            Uri[] result = null;
            if (resultCode == RESULT_OK && data != null) {
                if (data.getClipData() != null) {
                    int count = data.getClipData().getItemCount();
                    result = new Uri[count];
                    for (int i = 0; i < count; i++) result[i] = data.getClipData().getItemAt(i).getUri();
                } else if (data.getData() != null) {
                    result = new Uri[]{data.getData()};
                }
            }
            files.onReceiveValue(result);
            files = null;
        }
    }

    @Override
    public void onRequestPermissionsResult(int r, String[] p, int[] g) {
        super.onRequestPermissionsResult(r, p, g);
        if (r == LOC && geo != null) {
            boolean ok = false;
            for (int x : g) ok |= x == PackageManager.PERMISSION_GRANTED;
            geo.invoke(origin, ok, true);
            geo = null;
        }
    }
}
