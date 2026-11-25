package es.riegocerca.maps;
import android.app.Activity;import android.content.Intent;import android.webkit.JavascriptInterface;
public final class ImportBridge{private final Activity a;private final int code;public ImportBridge(Activity a,int code){this.a=a;this.code=code;}@JavascriptInterface public void importXlsx(){a.runOnUiThread(()->{Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");a.startActivityForResult(i,code);});}}
