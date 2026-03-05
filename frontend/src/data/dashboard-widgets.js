export const DASHBOARD_WIDGETS = [
  {
    id: 'summary-strip',
    label: 'Monthly Summary',
    icon: 'bar-chart-2',
    description: 'Income, expense & net balance this month',
  },
  {
    id: 'account-cards',
    label: 'Account Balances',
    icon: 'credit-card',
    description: 'Balance card for each account',
  },
  {
    id: 'equity-card',
    label: 'Equity',
    icon: 'trending-up',
    description: 'Total net worth across all accounts',
  },
  {
    id: 'bar-chart',
    label: 'Monthly Trend',
    icon: 'bar-chart',
    description: 'Income vs expense over the last 6 months',
  },
  {
    id: 'donut-chart',
    label: 'Category Breakdown',
    icon: 'pie-chart',
    description: 'Spending & income by category (swipeable)',
  },
]

export const DEFAULT_CONFIG = DASHBOARD_WIDGETS.map((w) => ({
  id: w.id,
  enabled: true,
}))
