package es.riegocerca.maps;
import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.*;

public class MainActivity extends Activity {
 private WebView web; private ValueCallback<Uri[]> files; private GeolocationPermissions.Callback geo; private String origin;
 private static final int LOC=7, FILE=8;
 @Override public void onCreate(Bundle state){super.onCreate(state);web=new WebView(this);setContentView(web);WebSettings s=web.getSettings();s.setJavaScriptEnabled(true);s.setDomStorageEnabled(true);s.setGeolocationEnabled(true);s.setAllowFileAccess(true);s.setAllowContentAccess(true);web.addJavascriptInterface(new MapsBridge(this),"AndroidMaps");web.setWebViewClient(new WebViewClient());web.setWebChromeClient(new WebChromeClient(){
  @Override public void onGeolocationPermissionsShowPrompt(String o,GeolocationPermissions.Callback c){origin=o;geo=c;if(checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)==PackageManager.PERMISSION_GRANTED||checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION)==PackageManager.PERMISSION_GRANTED){c.invoke(o,true,true);geo=null;origin=null;}else requestPermissions(new String[]{Manifest.permission.ACCESS_FINE_LOCATION,Manifest.permission.ACCESS_COARSE_LOCATION},LOC);}
  @Override public boolean onShowFileChooser(WebView v,ValueCallback<Uri[]> c,FileChooserParams p){files=c;try{startActivityForResult(p.createIntent(),FILE);return true;}catch(Exception e){files=null;return false;}}
 });if(state==null)web.loadUrl("file:///android_asset/index.html");else web.restoreState(state);}
 @Override public void onRequestPermissionsResult(int r,String[] p,int[] g){super.onRequestPermissionsResult(r,p,g);if(r==LOC&&geo!=null){boolean ok=false;for(int x:g)ok|=x==PackageManager.PERMISSION_GRANTED;geo.invoke(origin,ok,true);geo=null;origin=null;}}
 @Override protected void onActivityResult(int r,int c,Intent d){super.onActivityResult(r,c,d);if(r==FILE&&files!=null){files.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(c,d));files=null;}}
 @Override protected void onSaveInstanceState(Bundle state){web.saveState(state);super.onSaveInstanceState(state);}
 @Override public void onBackPressed(){if(web.canGoBack())web.goBack();else super.onBackPressed();}
}
