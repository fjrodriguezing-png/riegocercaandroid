package es.riegocerca.maps;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.webkit.JavascriptInterface;
import org.json.JSONArray;

public class MapsBridge {
    private final Activity activity;
    MapsBridge(Activity activity) { this.activity = activity; }

    @JavascriptInterface public void navigate(String coordinate) {
        open("https://www.google.com/maps/dir/?api=1&destination=" + Uri.encode(coordinate) + "&travelmode=driving");
    }

    @JavascriptInterface public void openMulti(String json) {
        try {
            JSONArray points = new JSONArray(json);
            if (points.length() == 0) return;
            String destination = points.getString(points.length() - 1);
            StringBuilder url = new StringBuilder("https://www.google.com/maps/dir/?api=1&destination=").append(Uri.encode(destination)).append("&travelmode=driving");
            if (points.length() > 1) {
                url.append("&waypoints=");
                for (int i = 0; i < points.length() - 1; i++) { if (i > 0) url.append("%7C"); url.append(Uri.encode(points.getString(i))); }
            }
            open(url.toString());
        } catch (Exception ignored) { }
    }

    private void open(String url) {
        activity.runOnUiThread(() -> {
            try { activity.startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url))); }
            catch (Exception ignored) { }
        });
    }
}
