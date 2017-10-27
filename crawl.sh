start=`date +%s`

rm -f scrapy.log

cat <<EOT >> scrapy.log
================================================================================
Crawling Genres from MangaFox
================================================================================
EOT

scrapy crawl mangafox_genres -L INFO

cat <<EOT >> scrapy.log


================================================================================
Crawling Index from MangaFox
================================================================================
EOT

scrapy crawl mangafox_index -L INFO

end=`date +%s`
runtime=$((end-start))

cat <<EOT >> scrapy.log

================================================================================
Runtime: $runtime seconds.

EOT
