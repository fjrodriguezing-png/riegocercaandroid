package es.riegocerca.maps;
import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.webkit.JavascriptInterface;
import org.json.JSONArray;
public class MapsBridge {
 private final Activity a; MapsBridge(Activity x){a=x;}
 @JavascriptInterface public void navigate(String c){open("https://www.google.com/maps/dir/?api=1&destination="+Uri.encode(c)+"&travelmode=driving");}
 @JavascriptInterface public void earth(String c){open("https://earth.google.com/web/search/"+Uri.encode(c));}
 @JavascriptInterface public void whatsapp(String text){open("https://wa.me/?text="+Uri.encode(text));}
 @JavascriptInterface public void openUrl(String url){open(url);}
 @JavascriptInterface public void openMulti(String json){try{JSONArray p=new JSONArray(json);if(p.length()==0)return;String d=p.getString(p.length()-1);StringBuilder u=new StringBuilder("https://www.google.com/maps/dir/?api=1&destination=").append(Uri.encode(d)).append("&travelmode=driving");if(p.length()>1){u.append("&waypoints=");for(int i=0;i<p.length()-1;i++){if(i>0)u.append("%7C");u.append(Uri.encode(p.getString(i)));}}open(u.toString());}catch(Exception ignored){}}
 private void open(String url){a.runOnUiThread(()->{try{a.startActivity(new Intent(Intent.ACTION_VIEW,Uri.parse(url)));}catch(Exception ignored){}});}
}
