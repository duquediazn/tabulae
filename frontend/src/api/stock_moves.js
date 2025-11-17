import API_URL from "./config";

export async function getStockMovements({
  accessToken,
  filters = {},
  limit = 10,
  offset = 0,
}) {
  const queryParams = new URLSearchParams();

  if (filters.searchTerm) queryParams.append("search", filters.searchTerm);
  if (filters.filterType) queryParams.append("move_type", filters.filterType);
  if (filters.dateFrom) queryParams.append("date_from", filters.dateFrom);
  if (filters.dateTo) queryParams.append("date_to", filters.dateTo);
  if (filters.userId) queryParams.append("user_id", filters.userId);

  queryParams.append("limit", limit);
  queryParams.append("offset", offset);

  const response = await fetch(
    `${API_URL}/stock-movements?${queryParams.toString()}`,
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );

  const data = await response.json();
  return {
    movements: data.data || [],
    total: data.total || 0,
  };
}

export async function countStockMovesByMoveType({ accessToken }) {
  const response = await fetch(`${API_URL}/stock-movements/summary/move-type`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  const data = await response.json();
  return data;
}

export async function getStockMovementById(id, accessToken) {
  const response = await fetch(`${API_URL}/stock-movements/${id}`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) throw new Error("Failed to load movement.");

  return await response.json();
}

export async function getMovementLines(id, accessToken, limit = 10, offset = 0) {
  const response = await fetch(
    `${API_URL}/stock-movements/${id}/lines?limit=${limit}&offset=${offset}`,
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );

  if (!response.ok)
    throw new Error("Failed to load movement lines.");

  return await response.json(); // { data: [...], total: n }
}

export async function createMovement(movement, accessToken) {
  const response = await fetch(`${API_URL}/stock-movements`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify(movement),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to register movement.");
  }

  return await response.json(); // MovementResponse object
}

export async function movementsLastYearByMonth(accessToken) {
  const response = await fetch(`${API_URL}/stock-movements/last-year`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  const data = await response.json();
  const movements = data || [];

  const groupBy = {};

  for (const mov of movements) {
    const date = new Date(mov.created_at);
    const key = `${date.getUTCFullYear()}-${String(
      date.getUTCMonth() + 1
    ).padStart(2, "0")}`;

    const moveType = mov.move_type.toLowerCase().trim();

    if (!groupBy[key]) {
      groupBy[key] = { month: key, incoming: 0, outgoing: 0 };
    }

    if (moveType === "incoming" || moveType === "outgoing") {
      groupBy[key][moveType]++;
    } else {
      console.warn("Unknown move type:", mov.move_type);
    }
  }

  return Object.values(groupBy).sort((a, b) => (a.month > b.month ? 1 : -1));
}
