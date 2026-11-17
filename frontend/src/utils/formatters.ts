export const formatCurrency = (value: number) => new Intl.NumberFormat('en-IN', {
  style: 'currency', currency: 'INR', maximumFractionDigits: 0,
}).format(value)

export const formatDateTime = (value?: string | null) => {
  if (!value) return 'Not available'
  return new Intl.DateTimeFormat('en-IN', {
    dateStyle: 'medium', timeStyle: 'short',
  }).format(new Date(value))
}

export const formatDateOnly = (value?: string | null) => {
  if (!value) return 'Not available'
  return new Intl.DateTimeFormat('en-IN', {
    dateStyle: 'medium',
  }).format(new Date(value))
}

export const formatNumber = (value: number) => new Intl.NumberFormat('en-IN').format(value)
