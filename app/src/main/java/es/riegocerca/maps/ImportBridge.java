package es.riegocerca.maps;

import android.app.Activity;
import android.content.Intent;
import android.webkit.JavascriptInterface;

public class ImportBridge {
    private final Activity activity;
    private final int requestCode;

    public ImportBridge(Activity activity, int requestCode) {
        this.activity = activity;
        this.requestCode = requestCode;
    }

    @JavascriptInterface
    public void importFile() {
        activity.runOnUiThread(() -> {
            Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
            intent.addCategory(Intent.CATEGORY_OPENABLE);
            intent.setType("*/*");
            intent.putExtra(Intent.EXTRA_MIME_TYPES, new String[]{
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "application/vnd.ms-excel",
                    "text/csv",
                    "text/comma-separated-values",
                    "application/csv"
            });
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);
            activity.startActivityForResult(intent, requestCode);
        });
    }
}
