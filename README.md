# Daily Pod (private feed)
Feed: https://earthnet-nz.github.io/vg-daily-pod-nx7xil/feed.xml — subscribe via "Follow a Show by URL" in Apple Podcasts or "Add URL" in Overcast.

## Add an episode
    ./add_episode.sh <audio-file-or-URL> "Title" "Description" [--start SECONDS] [--image FILE-or-URL] [--no-push] [--date "RFC822 date"]
Downloads (yt-dlp for URLs), converts to mono 64 kbps mp3 in episodes/, prepends the item to feed.xml, commits and pushes.
Keep files under 100 MB (GitHub limit). robots.txt and itunes:block keep it out of directories.

## Artwork (required on every episode)
Every <item> must carry its own <itunes:image>, and the channel keeps <itunes:image href=".../cover-art.jpg"/>.
- `--image FILE-or-URL` sets the episode art explicitly (local image, direct image URL, or a page URL yt-dlp can get a thumbnail from).
- Without `--image`, a URL source (YouTube, X, etc.) auto-fetches its thumbnail with yt-dlp.
- Art is converted to a 3000x3000 RGB JPG (thumbnail centred on a blurred fill) and saved as episodes/epNNN-<slug>-art.jpg (baseline, 72 dpi, kept under ~500 KB) and also embedded in the mp3 as ID3v2.3 APIC front cover (1400px) next to the mp3.
- If no image can be found (local audio file and no --image), the item falls back to cover-art.jpg, so always pass --image for local files.
