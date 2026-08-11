import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
export const formatCurrency = (value: number | string) =>
  new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(
    Number(value),
  );
export const formatNumber = (value: number | string, digits = 0) =>
  new Intl.NumberFormat("pt-BR", { maximumFractionDigits: digits }).format(
    Number(value),
  );
export const formatPercent = (value: number | string, digits = 1) =>
  `${formatNumber(value, digits)}%`;
export const titleCase = (value: string) =>
  value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
