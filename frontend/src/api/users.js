import API_URL from "./config";

export async function getUserById(id, accessToken) {
  const response = await fetch(`${API_URL}/users/${id}`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to fetch user data.");
  }

  return await response.json(); // { id, name, email, role, is_active }
}

export async function updateUser(id, token, data) {
  const payload = { ...data };
  if (!data.password) delete payload.password;

  const response = await fetch(`${API_URL}/users/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let message = "Failed to update profile.";

    try {
      const error = await response.json();

      if (Array.isArray(error.detail)) {
        message = error.detail.map((e) => e.msg).join("\n");
      }

      else if (typeof error.detail === "string") {
        message = error.detail;
      }
    } catch {
      message = await response.text();
    }

    throw new Error(message);
  }
  return await response.json();
}

export async function getUsers({
  accessToken,
  limit = 10,
  offset = 0,
  searchTerm = "",
  is_active = "",
}) {
  const url = new URL(`${API_URL}/users`);
  url.searchParams.append("limit", limit);
  url.searchParams.append("offset", offset);
  if (searchTerm?.trim()) url.searchParams.append("search", searchTerm);
  if (is_active === "true" || is_active === "false")
    url.searchParams.append("is_active", is_active);

  const response = await fetch(url.toString(), {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to fetch users.");
  }

  return await response.json(); // { data, total, limit, offset }
}

export async function usersBulkStatus(ids, is_active, accessToken) {
  const response = await fetch(`${API_URL}/users/bulk-status`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({ ids, is_active }),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || "Failed to update user status.");
  }

  return data; // { message, skipped }
}

export async function deleteUser(id, accessToken) {
  const response = await fetch(`${API_URL}/users/${id}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || "Failed to delete user.");
  }

  return data;
}

export async function createUser(data, accessToken) {
  const response = await fetch(`${API_URL}/users`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to create user.");
  }

  return await response.json();
}
