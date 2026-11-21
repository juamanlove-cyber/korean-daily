"""audio/list.tsv 의 문장을 자연스러운 한국어 음성(mp3)으로 만든다. 이미 있는 파일은 건너뛴다."""
import asyncio, json, os, edge_tts
VOICE = "ko-KR-SunHiNeural"
async def one(h, text, sem):
    path = f"audio/{h}.mp3"
    if os.path.exists(path) and os.path.getsize(path) > 0: return
    async with sem:
        for attempt in range(4):
            try:
                await edge_tts.Communicate(text, VOICE, rate="-10%").save(path); return
            except Exception as e:
                print("retry", text, e); await asyncio.sleep(2 + attempt * 3)
async def main():
    rows = [l.rstrip("\n").split("\t", 1) for l in open("audio/list.tsv", encoding="utf8") if "\t" in l]
    sem = asyncio.Semaphore(6)
    await asyncio.gather(*(one(h, t, sem) for h, t in rows))
    ok = sorted(h for h, _ in rows if os.path.exists(f"audio/{h}.mp3") and os.path.getsize(f"audio/{h}.mp3") > 0)
    json.dump(ok, open("audio/index.json", "w"))
    print(len(ok), "/", len(rows), "audio files")
asyncio.run(main())
