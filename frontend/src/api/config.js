if (!import.meta.env.VITE_API_URL) {
    throw new Error("VITE_API_URL not defined.");
}

const API_URL = import.meta.env.VITE_API_URL;
export default API_URL;
