async function shortenUrl() {
    const originalUrl = document.getElementById("originalUrl").value;

    try {
        const response = await fetch('/shorten_urls', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                url: originalUrl
            })
        });

        const data = await response.json();
        if (response.ok) {
            document.getElementById("shortenedUrl").innerText = `Shortened URL: ${data.Url.short_url}`;
        } else {
            document.getElementById("shortenedUrl").innerText = `Error: ${data.detail}`;
        }
    } catch (error) {
        console.error('Error:', error);
    }
}
