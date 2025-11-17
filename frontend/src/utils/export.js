/*CSV Export Utilities
This file provides reusable functions to export filtered data from various endpoints (e.g., movements, products, warehouses, users) to CSV format using PapaParse.
import Papa from "papaparse";
*/
import Papa from "papaparse";

// Generic function to export data from any endpoint as a CSV
export async function exportCSVGeneric({
  accessToken,
  apiUrl,
  endpoint,
  queryParams = {},
  filename = "export.csv",
  mapFn,
}) {
  try {
    // Build full URL with query parameters
    const url = new URL(`${apiUrl}${endpoint}`);
    for (const [key, value] of Object.entries(queryParams)) {
      if (
        value !== null &&
        value !== undefined &&
        !(typeof value === "string" && value.trim() === "")
      ) {
        url.searchParams.append(key, value);
      }
    }

    // Fetch data with authentication header
    const response = await fetch(url.toString(), {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    const data = await response.json();
    const items = data.data || [];

    // Convert data to CSV using PapaParse
    const csv = Papa.unparse(items.map(mapFn), { delimiter: ";" });
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const urlBlob = URL.createObjectURL(blob);

    // Trigger file download in browser
    const link = document.createElement("a");
    link.href = urlBlob;
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (error) {
    console.error("Error exporting CSV:", error);
    alert("An error occurred while exporting:\n" + error.message);
  }
}

/*Export Specific Datasets
Each function below configures the right filters and mapping logic to call the generic exporter for a specific resource.

exportFilteredMovementsCSV
*/

export async function exportFilteredMovementsCSV({
  accessToken,
  filters,
  apiUrl,
}) {
  const queryParams = {
    limit: 1000,
    offset: 0,
  };

  if (filters.searchTerm?.trim()) queryParams.search = filters.searchTerm;
  if (filters.filterType) queryParams.move_type = filters.filterType;
  if (filters.dateFrom) queryParams.from = filters.dateFrom;
  if (filters.dateTo) queryParams.to = filters.dateTo;
  if (filters.userId) queryParams.user_id = filters.userId;

  return exportCSVGeneric({
    accessToken,
    apiUrl,
    endpoint: "/stock-movements",
    queryParams,
    filename: "stock-movements.csv",
    mapFn: (m) => ({
      ID: m.move_id,
      Type: m.move_type,
      User: m.user_name,
      Date: new Date(m.created_at).toLocaleDateString(),
      Lines: m.lines?.length ?? 0,
    }),
  });
}

//exportFilteredProductsCSV

export async function exportFilteredProductsCSV({
  accessToken,
  filters,
  apiUrl,
}) {
  const queryParams = {
    limit: 1000,
    offset: 0,
  };

  if (filters.searchTerm?.trim()) queryParams.search = filters.searchTerm;
  if (filters.category_id) queryParams.category_id = filters.category_id;
  if (filters.isActive === "true" || filters.isActive === "false") {
    queryParams.is_active = filters.isActive === "true";
  }

  return exportCSVGeneric({
    accessToken,
    apiUrl,
    endpoint: "/products",
    queryParams,
    filename: "products.csv",
    mapFn: (p) => ({
      SKU: p.sku,
      Name: p.short_name,
      Category: p.category_name,
      Status: p.is_active ? "Active" : "Inactive",
    }),
  });
}


//exportFilteredWarehousesCSV

export async function exportFilteredWarehousesCSV({
  accessToken,
  apiUrl,
  filters,
}) {
  const queryParams = {
    limit: 1000,
    offset: 0,
  };

  if (filters.searchTerm?.trim()) queryParams.search = filters.searchTerm;
  if (filters.isActive === "true" || filters.isActive === "false") {
    queryParams.is_active = filters.isActive === "true";
  }

  return exportCSVGeneric({
    accessToken,
    apiUrl,
    endpoint: "/warehouses",
    queryParams,
    filename: "warehouses.csv",
    mapFn: (a) => ({
      ID: a.id,
      Description: a.description,
      Status: a.is_active ? "Active" : "Inactive",
    }),
  });
}

//exportFilteredUsersCSV

export async function exportFilteredUsersCSV({
  accessToken,
  filters,
  apiUrl,
}) {
  const queryParams = {
    limit: 1000,
    offset: 0,
  };

  if (filters.isActive === "true" || filters.isActive === "false") {
    queryParams.is_active = filters.isActive === "true";
  }
  if (filters.searchTerm?.trim()) {
    queryParams.search = filters.searchTerm;
  }

  return exportCSVGeneric({
    accessToken,
    apiUrl,
    endpoint: "/users",
    queryParams,
    filename: "users.csv",
    mapFn: (u) => ({
      ID: u.id,
      Name: u.name,
      Email: u.email,
      Role: u.role,
      Status: u.is_active ? "Active" : "Inactive",
    }),
  });
}
