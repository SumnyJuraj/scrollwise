const STORAGE_KEYS = {
  LIKED_FACTS: 'scrollwise_liked_facts',
  SAVED_FACTS: 'scrollwise_saved_facts',
  READ_FACTS: 'scrollwise_read_facts',
  SOUND_ENABLED: 'scrollwise_sound_enabled',
  LAST_READ_DATE: 'scrollwise_last_read_date',
  STREAK_COUNT: 'scrollwise_streak_count',
};

export const getLikedFactIds = (): string[] => {
  try {
    const data = localStorage.getItem(STORAGE_KEYS.LIKED_FACTS);
    return data ? JSON.parse(data) : [];
  } catch {
    return [];
  }
};

export const toggleLikedFactId = (id: string): { liked: boolean; allLiked: string[] } => {
  const current = getLikedFactIds();
  const exists = current.includes(id);
  const updated = exists ? current.filter((item) => item !== id) : [...current, id];
  try {
    localStorage.setItem(STORAGE_KEYS.LIKED_FACTS, JSON.stringify(updated));
  } catch (e) {
    console.error(e);
  }
  return { liked: !exists, allLiked: updated };
};

export const getSavedFactIds = (): string[] => {
  try {
    const data = localStorage.getItem(STORAGE_KEYS.SAVED_FACTS);
    return data ? JSON.parse(data) : [];
  } catch {
    return [];
  }
};

export const toggleSavedFactId = (id: string): { saved: boolean; allSaved: string[] } => {
  const current = getSavedFactIds();
  const exists = current.includes(id);
  const updated = exists ? current.filter((item) => item !== id) : [...current, id];
  try {
    localStorage.setItem(STORAGE_KEYS.SAVED_FACTS, JSON.stringify(updated));
  } catch (e) {
    console.error(e);
  }
  return { saved: !exists, allSaved: updated };
};

export const recordFactRead = (id: string): { totalRead: number; streak: number } => {
  try {
    const rawRead = localStorage.getItem(STORAGE_KEYS.READ_FACTS);
    const readList: string[] = rawRead ? JSON.parse(rawRead) : [];
    if (!readList.includes(id)) {
      readList.push(id);
      localStorage.setItem(STORAGE_KEYS.READ_FACTS, JSON.stringify(readList));
    }

    const todayStr = new Date().toISOString().slice(0, 10);
    const lastDate = localStorage.getItem(STORAGE_KEYS.LAST_READ_DATE);
    let streak = parseInt(localStorage.getItem(STORAGE_KEYS.STREAK_COUNT) || '1', 10);

    if (lastDate !== todayStr) {
      if (lastDate) {
        const diffDays = Math.floor(
          (new Date(todayStr).getTime() - new Date(lastDate).getTime()) / (1000 * 3600 * 24)
        );
        if (diffDays === 1) {
          streak += 1;
        } else if (diffDays > 1) {
          streak = 1;
        }
      }
      localStorage.setItem(STORAGE_KEYS.LAST_READ_DATE, todayStr);
      localStorage.setItem(STORAGE_KEYS.STREAK_COUNT, streak.toString());
    }

    return { totalRead: readList.length, streak };
  } catch {
    return { totalRead: 1, streak: 1 };
  }
};

export const getSoundPreference = (): boolean => {
  try {
    const val = localStorage.getItem(STORAGE_KEYS.SOUND_ENABLED);
    return val === null ? true : val === 'true';
  } catch {
    return true;
  }
};

export const setSoundPreference = (enabled: boolean): void => {
  try {
    localStorage.setItem(STORAGE_KEYS.SOUND_ENABLED, String(enabled));
  } catch (e) {
    console.error(e);
  }
};
