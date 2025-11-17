import API_URL from "./config";

export async function getSemaphore(accessToken) {
  const response = await fetch(`${API_URL}/stock/semaphore`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to fetch semaphore state.");
  }

  return await response.json(); // { no_expiry, expiring_soon, expired }
}

export async function getWarehouseDetail(accessToken) {
  const response = await fetch(`${API_URL}/stock/warehouses/detail`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to fetch warehouse detail.");
  }

  return await response.json();
}

export async function getProductsByWarehousePieChart(warehouseId, accessToken) {
  const response = await fetch(
    `${API_URL}/stock/warehouse/${warehouseId}/detail`,
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to fetch products by warehouse.");
  }

  return await response.json();
}

export async function getProductHistory(productId, accessToken, limit = 10, offset = 0) {
  const response = await fetch(
    `${API_URL}/stock/product/${productId}/history?limit=${limit}&offset=${offset}`,
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to fetch product history.");
  }

  return await response.json();
}

export async function getProductHistoryByWarehouse(
  warehouseId,
  productId,
  accessToken,
  limit = 100,
  offset = 0
) {
  const response = await fetch(
    `${API_URL}/stock/warehouse/${warehouseId}/product/${productId}/history?limit=${limit}&offset=${offset}`,
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to fetch product history.");
  }

  return await response.json();
}

export async function getStockByProduct(productId, accessToken, limit = 10, offset = 0) {
  const url = new URL(`${API_URL}/stock/product/${productId}`);
  url.searchParams.append("limit", limit);
  url.searchParams.append("offset", offset);

  const response = await fetch(url.toString(), {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to fetch stock by product.");
  }

  return await response.json();
}

export async function getStockByCategory(accessToken) {
  const res = await fetch(`${API_URL}/stock/product-categories`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!res.ok) {
    throw new Error("Failed to fetch stock by category.");
  }

  return await res.json();
}

export async function getProductsByCategory(categoryId, accessToken) {
  const res = await fetch(`${API_URL}/stock/category/${categoryId}/products`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!res.ok) {
    throw new Error("Failed to fetch products by category.");
  }

  return await res.json();
}

export async function getProductStockByWarehouse(
  warehouseId,
  productId,
  accessToken,
  limit = 10,
  offset = 0
) {
  const response = await fetch(
    `${API_URL}/stock/warehouse/${warehouseId}/product/${productId}?limit=${limit}&offset=${offset}`,
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to fetch product stock by warehouse.");
  }

  return await response.json();
}

export async function getStockByWarehouse(
  warehouseId,
  accessToken,
  limit = 10,
  offset = 0
) {
  const response = await fetch(
    `${API_URL}/stock/warehouse/${warehouseId}?limit=${limit}&offset=${offset}`,
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to fetch stock by warehouse.");
  }

  return await response.json();
}

export async function getWarehouseHistory(
  warehouseId,
  accessToken,
  limit = 100,
  offset = 0
) {
  const response = await fetch(
    `${API_URL}/stock/warehouse/${warehouseId}/history?limit=${limit}&offset=${offset}`,
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to fetch warehouse history.");
  }

  return await response.json();
}

export async function getAvailableLots({ productId, warehouseId, accessToken }) {
  const response = await fetch(
    `${API_URL}/stock/available-lots?product=${productId}&warehouse=${warehouseId}`,
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );

  if (!response.ok) {
    throw new Error("Failed to load available lots.");
  }

  return await response.json(); // [{ lot, expiration_date, quantity }]
}

export async function getExpiringProducts({ accessToken, fromMonths, rangeMonths, limit, offset }) {
  const url = new URL(`${API_URL}/stock/product/expiring`);
  url.searchParams.append("from_months", fromMonths);
  url.searchParams.append("range_months", rangeMonths);
  url.searchParams.append("limit", limit);
  url.searchParams.append("offset", offset);

  const response = await fetch(url.toString(), {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to fetch expiring products.");
  }

  return await response.json();
}
