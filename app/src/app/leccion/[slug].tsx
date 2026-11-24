import { useLocalSearchParams } from "expo-router";

import { LessonView } from "@/components/lesson/lesson-view";

export default function LessonScreen() {
  const { slug } = useLocalSearchParams<{ slug: string }>();
  return <LessonView key={slug} lessonSlug={slug} />;
}
