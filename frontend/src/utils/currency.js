/**
 * Format a number as currency with the given symbol.
 *
 * @param {number} value - Numeric amount
 * @param {string} symbol - Currency symbol (e.g. "Rs.", "$", "€")
 * @returns {string} Formatted string, e.g. "Rs. 1,212.00"
 */
export function formatCurrency(value, symbol = 'Rs.') {
  const formatted = Number(value || 0).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
  return `${symbol} ${formatted}`
}
