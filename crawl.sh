#!/usr/bin/env bash

# Backup old log
logfile="logs/scrapy.log"
if [ -f $logfile ]; then
   mv -f $logfile $logfile".old"
fi
mkdir -p "$(dirname "$logfile")" || exit
touch "$logfile"

cat <<EOT >> $logfile
================================================================================
Crawling Manga Genres from MangaFox
================================================================================
EOT

start=`date +%s`

scrapy crawl mangafox_genres -L INFO --logfile="$logfile"

end=`date +%s`
runtime=$((end-start))

cat <<EOT >> $logfile


================================================================================
Crawling Manga Index from MangaFox
================================================================================
EOT

scrapy crawl mangafox_index -L INFO --logfile="$logfile"

end=`date +%s`
runtime=$((runtime+end-start))

cat <<EOT >> $logfile

================================================================================
Runtime: $runtime seconds.

EOT
