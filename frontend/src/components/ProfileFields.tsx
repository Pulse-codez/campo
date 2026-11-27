"use client";

import type { Gender, StudyField, VoicePreference } from "@/lib/api";

export interface ProfileValues {
  gender: Gender | "";
  year_of_study: string;
  field_of_study: StudyField;
  voice_preference: VoicePreference;
}

interface Props {
  values: ProfileValues;
  onChange: (next: ProfileValues) => void;
}

/** Broad, non-identifying profile used for peer matching and voice choice. */
export default function ProfileFields({ values, onChange }: Props) {
  const set = <K extends keyof ProfileValues>(key: K, value: ProfileValues[K]) =>
    onChange({ ...values, [key]: value });

  return (
    <section className="panel space-y-4">
      <div>
        <h2 className="font-semibold">About you</h2>
        <p className="text-sm text-[rgba(238,243,255,0.6)] mt-1">
          Only broad details. Used to find a peer who has faced something similar and to pick a voice.
        </p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className="label" htmlFor="gender">Gender</label>
          <select
            id="gender"
            className="input"
            value={values.gender}
            onChange={(e) => set("gender", e.target.value as ProfileValues["gender"])}
          >
            <option value="">Prefer not to say</option>
            <option value="female">Female</option>
            <option value="male">Male</option>
            <option value="non_binary">Non-binary</option>
            <option value="prefer_not_to_say">Prefer not to say</option>
          </select>
        </div>
        <div>
          <label className="label" htmlFor="year">Year of study</label>
          <select
            id="year"
            className="input"
            value={values.year_of_study}
            onChange={(e) => set("year_of_study", e.target.value)}
          >
            <option value="">Not sure yet</option>
            {[1, 2, 3, 4, 5, 6].map((year) => (
              <option key={year} value={year}>
                Year {year}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="label" htmlFor="field">Field of study</label>
          <select
            id="field"
            className="input"
            value={values.field_of_study}
            onChange={(e) => set("field_of_study", e.target.value as StudyField)}
          >
            <option value="tech">Tech</option>
            <option value="art">Art</option>
            <option value="other">Other</option>
          </select>
        </div>
        <div>
          <label className="label" htmlFor="voice">Read-aloud voice</label>
          <select
            id="voice"
            className="input"
            value={values.voice_preference}
            onChange={(e) => set("voice_preference", e.target.value as VoicePreference)}
          >
            <option value="auto">Auto (opposite gender)</option>
            <option value="female">Female voice</option>
            <option value="male">Male voice</option>
          </select>
        </div>
      </div>
    </section>
  );
}
