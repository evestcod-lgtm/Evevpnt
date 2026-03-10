[app]
title = EVEVPN
package.name = evevpn
package.domain = org.eve.vpn
source.dir = .
source.include_exts = py,png,jpg,json,xray
version = 1.0

requirements = python3,flask,kivy,android,requests

orientation = portrait
fullscreen = 1
android.archs = arm64-v8a

android.permissions = INTERNET,FOREGROUND_SERVICE,VIBRATE,ACCESS_NETWORK_STATE,CHANGE_NETWORK_STATE

android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b

android.foreground_service = true
android.wakelock = true

python-for-android.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
