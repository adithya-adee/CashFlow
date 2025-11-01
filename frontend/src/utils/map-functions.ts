export const CURRENCY_SYMBOLS = {
  INR: '₹',
  USD: '$',
  JPY: '¥',
} as const;

export type CurrencyCode = keyof typeof CURRENCY_SYMBOLS;

export function mapCurrencyToSymbol(code: string): string {
  if (code in CURRENCY_SYMBOLS) {
    return CURRENCY_SYMBOLS[code as CurrencyCode];
  }
  return '$';
}
