import json

def html_transcription(transcription, speakers, audio_file):
    html_segments = "\n".join([
        f"""<p>
                <button class="play-button" data-start=\"{s['timestamp'][0]}\" data-end=\"{s['timestamp'][1]}\">
                    ▶
                </button>
                <strong>{speakers[s['speaker']]}:</strong> {s['text']}
            <p>""" for s in transcription
    ])

    js = """
    const audio = document.querySelector("audio#audio");
    let endingAt = null;
    function playSegment(event){
        audio.currentTime = Number(event.target.getAttribute("data-start"));
        endingAt = Number(event.target.getAttribute("data-end"));
        audio.play();
    }
    document.querySelectorAll(".play-button").forEach(b => b.addEventListener("click", playSegment));
    audio.addEventListener("timeupdate", () => {
        if (endingAt !== null && audio.currentTime >= endingAt){
            audio.pause();
            endingAt = null;
        }
    });
    """

    html = f"""<!DOCTYPE html>
    <html>
    <head>
    <title>Mitch's Sane & Coherent Meeting Transcriptions 'R' Us</title>
    </head>
    <body>
        <audio controls src="{audio_file}" id="audio"></audio>
        {html_segments}
        <script>
            {js}
        </script>
    </body>
    </html>
    """
    return html


if __name__ == "__main__":
    speakers = {
        "SPEAKER_00": "Gertrude",
        "SPEAKER_01": "Philip"
    }
    transcription = json.load(open("test.mp3.json"))
    html = html_transcription(transcription, speakers, "test.mp3")
    open("test.mp3.html", mode="w+", encoding="utf-8").write(html)
