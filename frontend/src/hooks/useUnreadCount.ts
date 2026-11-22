import { useAppStore } from "../store/AppStore";

/** Number of unread notifications in the store. */
export function useUnreadCount(): number {
  const { notifications } = useAppStore();
  return notifications.filter((item) => !item.read).length;
}
