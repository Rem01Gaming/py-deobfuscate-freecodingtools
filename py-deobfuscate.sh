cp $1 1.tmp
sed -i 's/exec/print/g' 1.tmp
python 1.tmp >2.tmp
layer=1

while true; do
	if cat 2.tmp | grep exec >/dev/null; then
		enc="$(sed -E "s/.*'(.*)'.*/\1/" 2.tmp)"
		echo "_ = lambda __ : __import__('zlib').decompress(__import__('base64').b64decode(__[::-1]));print((_)(b'$enc'))" >2.tmp
		enc2="$(python 2.tmp)"
		echo $enc2 >2.tmp
		echo -ne -e "Deobfuscating layer $layer...\r"
		((layer++))
	else
		rm 1.tmp
		mv 2.tmp $1.dec
		echo "Deobfuscated script: $1.dec"
		exit 0
	fi
done
