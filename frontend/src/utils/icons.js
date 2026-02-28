/**
 * Icon utility for Nexus Books.
 *
 * lucide-static exports all Lucide SVGs as string constants under PascalCase names.
 * This module converts kebab-case icon names (e.g. "shopping-cart") to the
 * PascalCase key (e.g. "ShoppingCart") and returns the ready-to-use SVG string.
 */
import * as LucideStatic from 'lucide-static'

/**
 * Convert a Lucide kebab-case icon name to its PascalCase export key.
 * Example: "shopping-cart" → "ShoppingCart"
 */
function kebabToPascal(iconName) {
  return iconName
    .split('-')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join('')
}

/**
 * Return the SVG string for a Lucide icon by its kebab-case name.
 * Returns an empty string if the icon name is not found.
 *
 * @param {string} iconName - Lucide kebab-case name, e.g. "shopping-cart"
 * @returns {string} SVG markup string
 */
export function getIconSvg(iconName) {
  if (!iconName) return ''
  return LucideStatic[kebabToPascal(iconName)] || ''
}
