# Daily Pod (private feed)
Feed: https://earthnet-nz.github.io/vg-daily-pod-nx7xil/feed.xml — subscribe via "Follow a Show by URL" in Apple Podcasts or "Add URL" in Overcast.

## Add an episode
    ./add_episode.sh <audio-file-or-URL> "Title" "Description" [--start SECONDS] [--no-push] [--date "RFC822 date"]
Downloads (yt-dlp for URLs), converts to mono 64 kbps mp3 in episodes/, prepends the item to feed.xml, commits and pushes.
Keep files under 100 MB (GitHub limit). robots.txt and itunes:block keep it out of directories.
