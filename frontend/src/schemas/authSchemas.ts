import { z } from "zod";

/**
 * Mirrors the validation in backend/app/schemas/user.py:
 * - password: min 8, max 128 chars, at least one letter and one digit
 * - full_name: min 1, max 100 chars
 * Matching it client-side lets us show the error before a round trip,
 * but the backend remains the source of truth.
 */
export const registerSchema = z
  .object({
    full_name: z.string().min(1, "Full name is required").max(100),
    email: z.string().email("Enter a valid email address"),
    password: z
      .string()
      .min(8, "Password must be at least 8 characters")
      .max(128)
      .refine((value) => /[0-9]/.test(value), "Password must contain at least one digit")
      .refine((value) => /[a-zA-Z]/.test(value), "Password must contain at least one letter"),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  });

export type RegisterFormValues = z.infer<typeof registerSchema>;

export const loginSchema = z.object({
  email: z.string().email("Enter a valid email address"),
  password: z.string().min(1, "Password is required"),
});

export type LoginFormValues = z.infer<typeof loginSchema>;
