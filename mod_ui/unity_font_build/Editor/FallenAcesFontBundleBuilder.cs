// Unity editor script: builds a TextMeshPro font asset into an asset bundle
// for XUnity.AutoTranslator's FallbackFontTextMeshPro / OverrideFontTextMeshPro.
//
// HOW TO USE:
//   1. Unity 6000 (must match the game's Unity version: Fallen Aces = Unity 6000.3.10).
//   2. Import TextMeshPro. Place DejaVuSans-Regular.ttf (or any redistributable
//      Cyrillic .ttf) in Assets/. Create a TMP Font Asset from it via
//      Window -> TextMeshPro -> Font Asset Creator (Unicode Range including 0400-04FF,
//      Padding 3-5, Packing Method Fast, Atlas Resolution 8192x8192).
//   3. Create folder Assets/Editor, put this file there.
//   4. In the Font Asset Creator, assign the generated font to AssetBundle
//      "fallenaces_cyr_ru" (via the object inspector: AssetBundle dropdown).
//   5. Menu: FallenAces UI Localization -> Build Font Bundle.
//   6. Copy the produced file "fallenaces_cyr_ru" (no extension) to the GAME ROOT,
//      and set in BepInEx/config/AutoTranslatorConfig.ini:
//          [Behaviour]
//          FallbackFontTextMeshPro=fallenaces_cyr_ru
//      (switch to OverrideFontTextMeshPro if the fallback path does not apply).
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

public static class FallenAcesFontBundleBuilder
{
    [MenuItem("FallenAces UI Localization/Build Font Bundle")]
    public static void BuildFontBundle()
    {
        const string bundleName = "fallenaces_cyr_ru";
        const string outputDir = "Builds/FontBundle";
        System.IO.Directory.CreateDirectory(outputDir);

        // Build target must match the game's 64-bit Windows Mono build.
        AssetBundleBuild[] buildMap = new AssetBundleBuild[]
        {
            new AssetBundleBuild
            {
                assetBundleName = bundleName,
                assetNames = new[] { "Assets/Fonts/DejaVuSans SDF.asset" } // <- path to your TMP font asset
            }
        };

        BuildReport report = BuildPipeline.BuildAssetBundles(outputDir, buildMap,
            BuildAssetBundleOptions.None, BuildTarget.StandaloneWindows64);

        if (report == null || report.summary.result != BuildResult.Succeeded)
        {
            Debug.LogError("Font bundle build FAILED. See console for details.");
            return;
        }

        string source = System.IO.Path.Combine(outputDir, bundleName);
        string dest = System.IO.Path.Combine("Builds", bundleName);
        System.IO.File.Copy(source, dest, true);
        Debug.Log($"Font bundle built: {dest}  (copy this file to the game root)");
    }
}
