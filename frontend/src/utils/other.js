// Utility: generateColors(n)
// Dynamically generates `n` distinct colors using HSL format
export function generateColors(n) {
    const colors = [];
    for (let i = 0; i < n; i++) {
        const hue = (i * 360) / n; // Distributes hues evenly around the color wheel
        colors.push(`hsl(${hue}, 70%, 50%)`);
    }
    return colors;
}

// Usage example:
// const chartColors = generateColors(5);
// ➝ ['hsl(0, 70%, 50%)', 'hsl(72, 70%, 50%)', ...]
