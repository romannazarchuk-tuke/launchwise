import {
  Briefcase, Calendar, CalendarCheck, CalendarDays, Circle, Clock, Coffee, CreditCard, Flag, Globe,
  Image as ImageIcon, Images, Languages, Layers, Mail, Map as MapIcon, MapPin, Megaphone, MessageSquare,
  Newspaper, Palette, PhoneCall, Rocket, Scissors, ShoppingBag, ShoppingCart, Sprout, Star, Utensils,
  Wrench, Zap, type LucideIcon,
} from "lucide-react";

/**
 * The backend's /api/options sends lucide icon names ("calendar-check").
 * An explicit map keeps the bundle small (no "load every icon" import).
 */
const ICONS: Record<string, LucideIcon> = {
  briefcase: Briefcase, calendar: Calendar, "calendar-check": CalendarCheck, "calendar-days": CalendarDays,
  clock: Clock, coffee: Coffee, "credit-card": CreditCard, flag: Flag, globe: Globe, image: ImageIcon,
  images: Images, languages: Languages, layers: Layers, mail: Mail, map: MapIcon, "map-pin": MapPin,
  megaphone: Megaphone, "message-square": MessageSquare, newspaper: Newspaper, palette: Palette,
  "phone-call": PhoneCall, rocket: Rocket, scissors: Scissors, "shopping-bag": ShoppingBag,
  "shopping-cart": ShoppingCart, sprout: Sprout, star: Star, utensils: Utensils, wrench: Wrench, zap: Zap,
};

export function OptionIcon({ name, className = "size-5" }: { name?: string; className?: string }) {
  const Icon = (name && ICONS[name]) || Circle;
  return <Icon className={className} aria-hidden="true" />;
}
