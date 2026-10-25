// Central API client for WLAN Observatory
const API = {
  async get(url) {
    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      return await res.json();
    } catch (err) {
      console.error(`API GET error: ${url}`, err);
      throw err;
    }
  },

  async post(url, data) {
    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      return await res.json();
    } catch (err) {
      console.error(`API POST error: ${url}`, err);
      throw err;
    }
  },
};
