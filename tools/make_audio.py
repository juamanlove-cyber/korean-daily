"""audio/list.tsv 의 문장을 자연스러운 한국어 음성(mp3)으로 만든다. 이미 있는 파일은 건너뛴다."""
import asyncio, json, os, edge_tts
VOICE = "ko-KR-SunHiNeural"
async def one(h, text, sem):
    path = f"audio/{h}.mp3"
    if os.path.exists(path) and os.path.getsize(path) > 0: return
    async with sem:
        for attempt in range(4):
            try:
                await asyncio.wait_for(edge_tts.Communicate(text, VOICE, rate="-10%").save(path), 40); print("ok", h, flush=True); return
            except Exception as e:
                print("retry", h, repr(e)[:200], flush=True); await asyncio.sleep(2 + attempt * 3)
async def main():
    rows = [l.rstrip("\n").split("\t", 1) for l in open("audio/list.tsv", encoding="utf8") if "\t" in l]
    # 먼저 한 개로 연결 확인 (실패하면 바로 중단)
    await asyncio.wait_for(edge_tts.Communicate("안녕하세요?", VOICE).save("/tmp/probe.mp3"), 40)
    sem = asyncio.Semaphore(4)
    await asyncio.gather(*(one(h, t, sem) for h, t in rows))
    ok = sorted(h for h, _ in rows if os.path.exists(f"audio/{h}.mp3") and os.path.getsize(f"audio/{h}.mp3") > 0)
    json.dump(ok, open("audio/index.json", "w"))
    print(len(ok), "/", len(rows), "audio files")
asyncio.run(main())
