package es.riegocerca.maps;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.net.Uri;
import android.webkit.JavascriptInterface;
import android.widget.Toast;

public class MapsBridge {
    private final Activity activity;
    public MapsBridge(Activity activity) { this.activity = activity; }

    @JavascriptInterface
    public void navigate(double lat, double lon) {
        if (!Double.isFinite(lat) || !Double.isFinite(lon) || lat < -90 || lat > 90 || lon < -180 || lon > 180) {
            activity.runOnUiThread(() -> Toast.makeText(activity, "Coordenadas GPS no válidas", Toast.LENGTH_LONG).show());
            return;
        }
        activity.runOnUiThread(() -> {
            Uri nativeUri = Uri.parse("google.navigation:q=" + lat + "," + lon + "&mode=d");
            Intent maps = new Intent(Intent.ACTION_VIEW, nativeUri);
            maps.setPackage("com.google.android.apps.maps");
            try {
                activity.startActivity(maps);
            } catch (ActivityNotFoundException ex) {
                Uri web = Uri.parse("https://www.google.com/maps/dir/?api=1&destination=" + lat + "," + lon + "&travelmode=driving");
                try { activity.startActivity(new Intent(Intent.ACTION_VIEW, web)); }
                catch (Exception e) { Toast.makeText(activity, "No se pudo abrir Google Maps", Toast.LENGTH_LONG).show(); }
            }
        });
    }
}
