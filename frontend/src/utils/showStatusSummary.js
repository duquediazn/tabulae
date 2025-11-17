// Utility: showStatusSummary(res, type = "items", action = "updated")
// Displays a summary message after performing a batch action
export function showStatusSummary(
  res,
  type = "items",
  action = "updated"
) {
  // Use the custom message if available; otherwise, build a default one
  const message =
    res.message || `${res.updated?.length || 0} ${type} ${action}`;
  const skipped = res.skipped || 0;

  // Show an alert with the summary and the number of skipped items if any
  if (skipped > 0) {
    alert(`${message}.\n${skipped} ${type} were skipped.`);
  } else {
    alert(message);
  }
}


/*
showStatusSummary(
  { updated: [1, 2, 3], skipped: 1 },
  "products",
  "activated"
);
// ➝ alert: "3 products activated.\n1 products were skipped."
*/