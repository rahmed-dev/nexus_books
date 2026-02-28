/**
 * Curated icon name list for the Nexus icon picker.
 *
 * Icons are loaded dynamically from lucide-static at render time — no static
 * imports here. Each name is a Lucide kebab-case icon name that maps directly
 * to lucide-static/dist/esm/icons/{name}.js.
 *
 * lucideIconGroups — names grouped by theme (display order in the picker)
 * allLucideIconNames — flat array of all curated names (for search filtering)
 */

export const lucideIconGroups = {
  Finance: [
    'credit-card', 'wallet', 'banknote', 'coins', 'piggy-bank', 'landmark',
    'trending-up', 'trending-down', 'receipt', 'calculator', 'percent',
    'dollar-sign', 'circle-dollar-sign', 'hand-coins', 'briefcase',
    'arrow-up-right', 'arrow-down-right', 'badge-dollar-sign',
  ],
  Shopping: [
    'shopping-cart', 'shopping-bag', 'store', 'package', 'tag', 'gift',
    'ticket', 'barcode', 'scan',
  ],
  'Food & Drink': [
    'coffee', 'cup-soda', 'utensils', 'pizza', 'apple', 'sandwich', 'wine',
    'beer', 'ice-cream-cone', 'cake', 'cookie', 'salad', 'fish', 'carrot',
    'egg', 'chef-hat',
  ],
  Transport: [
    'car', 'bus', 'train', 'plane', 'bicycle', 'fuel', 'truck', 'ship',
    'navigation', 'map-pin', 'traffic-cone', 'motorcycle',
  ],
  Home: [
    'home', 'building', 'building-2', 'key', 'bed', 'sofa', 'lamp', 'tv',
    'thermometer', 'plug', 'wifi', 'wrench', 'hammer', 'paintbrush',
    'washing-machine', 'bath',
  ],
  Health: [
    'heart', 'activity', 'dumbbell', 'pill', 'stethoscope', 'cross',
    'syringe', 'baby', 'eye', 'brain', 'heart-pulse', 'ambulance',
  ],
  Entertainment: [
    'music', 'music-2', 'headphones', 'film', 'gamepad-2', 'book-open',
    'camera', 'mic', 'monitor-play', 'party-popper', 'clapperboard', 'dices',
    'palette', 'pen-tool',
  ],
  Tech: [
    'smartphone', 'laptop', 'tablet', 'keyboard', 'printer', 'server', 'cpu',
    'hard-drive', 'bluetooth', 'battery', 'battery-charging', 'monitor',
  ],
  'Personal & Social': [
    'user', 'users', 'graduation-cap', 'award', 'star', 'smile', 'handshake',
    'heart-handshake', 'user-round', 'users-round',
  ],
  Nature: [
    'sun', 'moon', 'cloud', 'umbrella', 'leaf', 'mountain', 'waves',
    'snowflake', 'wind', 'flower-2', 'flame', 'zap', 'droplets', 'paw-print',
  ],
  'Work & Utilities': [
    'scissors', 'trash-2', 'folder', 'file-text', 'paperclip', 'pen', 'mail',
    'phone', 'message-circle', 'bell', 'calendar', 'clock', 'settings',
    'globe', 'lock', 'shield', 'bookmark', 'link',
  ],
}

export const allLucideIconNames = Object.values(lucideIconGroups).flat()
