import math
from pathlib import Path

from mido import Message, MidiFile, MidiTrack, MetaMessage, bpm2tempo, second2tick


DEFAULT_BPM = 120
TICKS_PER_BEAT = 480


def _frequency_to_midi_note(frequency: float) -> int:
    midi_note = 69 + 12 * math.log2(frequency / 440.0)
    return max(0, min(127, int(round(midi_note))))


def generate_midi_from_pitch(pitch_data: dict, output_filename: str) -> str:
    notes = pitch_data.get("notes", [])
    if not isinstance(notes, list):
        raise ValueError("pitch_data['notes'] must be a list")

    temp_midi_dir = Path("temp_midi")
    temp_midi_dir.mkdir(parents=True, exist_ok=True)

    midi_path = (temp_midi_dir / output_filename).with_suffix(".mid")

    midi_file = MidiFile(ticks_per_beat=TICKS_PER_BEAT)
    track = MidiTrack()
    midi_file.tracks.append(track)

    tempo = bpm2tempo(DEFAULT_BPM)
    track.append(MetaMessage("set_tempo", tempo=tempo, time=0))

    events: list[tuple[float, str, int]] = []
    for note in notes:
        if not isinstance(note, dict):
            continue

        start_time = note.get("start")
        end_time = note.get("end")
        pitch_value = note.get("pitch")
        frequency = note.get("frequency")

        if start_time is None or end_time is None:
            continue
        if end_time <= start_time:
            continue

        midi_note = None
        if isinstance(pitch_value, (int, float)):
            if 0 <= int(round(pitch_value)) <= 127:
                midi_note = int(round(pitch_value))
            elif pitch_value > 0:
                midi_note = _frequency_to_midi_note(float(pitch_value))
        elif isinstance(frequency, (int, float)) and frequency > 0:
            midi_note = _frequency_to_midi_note(float(frequency))

        if midi_note is None:
            continue

        events.append((float(start_time), "note_on", midi_note))
        events.append((float(end_time), "note_off", midi_note))

    events.sort(key=lambda event: (event[0], 0 if event[1] == "note_off" else 1))

    previous_tick = 0
    for time_seconds, event_type, midi_note in events:
        absolute_tick = int(round(second2tick(time_seconds, TICKS_PER_BEAT, tempo)))
        delta_tick = max(0, absolute_tick - previous_tick)
        velocity = 64 if event_type == "note_on" else 0
        track.append(Message(event_type, note=midi_note, velocity=velocity, time=delta_tick))
        previous_tick = absolute_tick

    midi_file.save(str(midi_path))
    return str(midi_path.resolve())