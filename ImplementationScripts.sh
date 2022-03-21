
# back button - with report
# prun SSIM-withReport.py -a <app name> -b <bugId> -l <lastImage.png>
prun SSIM-withReport.py -a k9mail -b 164 -l com.fsck.k9.User-Trace.12.com.fsck.k9_164_k9mail8.png
prun SSIM-withReport.py -a focus -b 272 -l org.mozilla.focus.User-Trace.12.org.mozilla.focus_272_focus11.png
prun SSIM-withReport.py -a Hex -b 1481 -l com.hexforhn.hex.User-Trace.12.com.hexforhn.hex_1481_Hex5.png

# back button - without report
# prun SSIM-withoutReport.py -a <app name> -b <bugId> 
prun SSIM-withoutReport.py -a k9mail -b 164
prun SSIM-withoutReport.py -a focus -b 272
prun SSIM-withoutReport.py -a Hex -b 1481


#theme change - without report
# prun themeCheck.py -a <app name> -b <bugId> 
prun themeCheck.py -a Simplenote -b 125
prun themeCheck.py -a phimpme-1398 -b 1398

#language detection - with and without report
# prun detectLanguage.py -a <app name> -b <bugId> 
prun detectLanguage.py -a Aegis -b 155 
prun detectLanguage.py -a andOtp -b 128

#orientation change - without report
prun findRotationCheckInput.py -a PuntiBuraco -b 1344
prun findRotationCheckInput.py -a AntennaPod -b 73   
prun findRotationCheckInput.py -a Anki -b 273     



#user entered data -  with report
prun compareText.py 123/25 null additional
prun compareText.py 157/12 \<world\> missing
prun compareText.py 266/4 m missing

#user entered data -  without report
prun findTriggerCheckInput.py AnglersLog 1441


#user selected data - without report
prun findTriggerCheckSelection.py GnuCash-1222 1222
prun findTriggerCheckSelection.py 142_QKSMS 142


