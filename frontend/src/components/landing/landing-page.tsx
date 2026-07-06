"use client";

import Link from "next/link";
import {
  ArrowRight,
  BrainCircuit,
  Database,
  LineChart,
  MapPin,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { motion, useReducedMotion } from "motion/react";
import { LandingHeroMap } from "@/components/landing/landing-hero-map";
import { LandingNav } from "@/components/landing/landing-nav";
import { FLOATING_NAV_HERO_OFFSET } from "@/components/layout/floating-glass-nav";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

const STATS = [
  { value: "15", label: "variables ML" },
  { value: "5", label: "fuentes abiertas" },
  { value: "SHAP", label: "explicabilidad" },
] as const;

const CAPABILITIES = [
  {
    icon: Database,
    title: "Integración multifuente",
    description:
      "Morbilidad SIVIGILA, vacunación, PM2.5 y acceso a salud consolidados por municipio y semana epidemiológica.",
  },
  {
    icon: BrainCircuit,
    title: "Random Forest + validación temporal",
    description:
      "Modelo predictivo entrenado con split temporal. Probabilidad de brote calibrada para apoyo analítico.",
  },
  {
    icon: Sparkles,
    title: "Contribuciones SHAP",
    description:
      "Cada predicción muestra qué variables empujan la señal hacia arriba o hacia abajo, en lenguaje claro.",
  },
  {
    icon: MapPin,
    title: "Radar territorial",
    description:
      "Ranking de alertas, mapa de señales y ficha por municipio para priorizar revisión humana.",
  },
] as const;

const DATASETS = [
  "SIVIGILA · morbilidad",
  "Vacunación DPT-HepB-Hib",
  "PM2.5 municipal",
  "Partos institucionales",
  "Catálogo DIVIPOLA",
] as const;

const STEPS = [
  {
    step: "01",
    title: "Ingesta y curación",
    body: "Sincronización desde datos.gov.co con validación territorial y trazabilidad por corrida.",
  },
  {
    step: "02",
    title: "Modelado explicable",
    body: "15 features derivadas alimentan un Random Forest promovido con métricas documentadas.",
  },
  {
    step: "03",
    title: "Decisión asistida",
    body: "Alertas, mapa e informe traducen la señal en insights accionables — sin activación automática.",
  },
] as const;

function Reveal({
  children,
  className,
  delay = 0,
}: {
  children: React.ReactNode;
  className?: string;
  delay?: number;
}) {
  const reduceMotion = useReducedMotion();

  return (
    <motion.div
      initial={reduceMotion ? false : { opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-60px" }}
      transition={{ duration: 0.55, delay, ease: [0.22, 1, 0.36, 1] }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

export function LandingPage() {
  const reduceMotion = useReducedMotion();

  return (
    <div className="landing-page relative min-h-screen overflow-x-hidden">
      <div className="landing-mesh pointer-events-none absolute inset-0" aria-hidden />
      <LandingNav />

      <main>
        {/* Hero */}
        <section
          className={cn(
            "relative mx-auto grid max-w-6xl gap-12 px-5 pb-20 md:grid-cols-2 md:items-center md:gap-16 md:px-8 md:pb-28 md:pt-28",
            FLOATING_NAV_HERO_OFFSET,
          )}
        >
          <div className="space-y-8">
            <motion.p
              initial={reduceMotion ? false : { opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.45 }}
              className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-3 py-1 text-xs font-medium tracking-wide text-primary uppercase"
            >
              <LineChart className="size-3.5" />
              Salud y Bienestar · Datos Abiertos 2026
            </motion.p>

            <motion.div
              initial={reduceMotion ? false : { opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.08, ease: [0.22, 1, 0.36, 1] }}
              className="space-y-5"
            >
              <h1 className="font-heading text-4xl leading-[1.08] tracking-tight text-balance md:text-5xl lg:text-[3.25rem]">
                Anticipa brotes con datos abiertos e IA explicable
              </h1>
              <p className="max-w-xl text-base leading-relaxed text-muted-foreground md:text-lg">
                Plataforma de inteligencia epidemiológica territorial para Colombia. Integra
                morbilidad, vacunación, calidad del aire y acceso a salud en un radar accionable
                con Random Forest y SHAP.
              </p>
            </motion.div>

            <motion.div
              initial={reduceMotion ? false : { opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.55, delay: 0.18 }}
              className="flex flex-wrap gap-3"
            >
              <Button render={<Link href="/radar" />} size="lg" className="gap-2 px-5">
                Abrir radar territorial
                <ArrowRight className="size-4" />
              </Button>
              <Button
                render={<Link href="/brotes" />}
                variant="outline"
                size="lg"
                className="px-5"
              >
                Ver ficha de brotes
              </Button>
            </motion.div>

            <motion.div
              initial={reduceMotion ? false : { opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.35, duration: 0.5 }}
              className="grid grid-cols-3 gap-4 border-t border-border/50 pt-6"
            >
              {STATS.map((stat) => (
                <div key={stat.label}>
                  <p className="font-mono text-2xl font-semibold text-primary md:text-3xl">
                    {stat.value}
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground md:text-sm">{stat.label}</p>
                </div>
              ))}
            </motion.div>
          </div>

          <motion.div
            initial={reduceMotion ? false : { opacity: 0, scale: 0.94 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.75, delay: 0.12, ease: [0.22, 1, 0.36, 1] }}
          >
            <LandingHeroMap />
          </motion.div>
        </section>

        {/* Capabilities */}
        <section id="capacidades" className="border-t border-border/40 bg-card/40 py-20 md:py-28">
          <div className="mx-auto max-w-6xl px-5 md:px-8">
            <Reveal className="mx-auto mb-14 max-w-2xl text-center">
              <p className="text-xs font-medium tracking-widest text-primary uppercase">
                Capacidades
              </p>
              <h2 className="mt-3 font-heading text-3xl tracking-tight md:text-4xl">
                De datos abiertos a señales territoriales
              </h2>
              <p className="mt-4 text-muted-foreground">
                Diseñado para analistas de salud pública: reproducible, auditable y sin caja negra.
              </p>
            </Reveal>

            <div className="grid gap-5 sm:grid-cols-2">
              {CAPABILITIES.map((item, index) => (
                <Reveal key={item.title} delay={index * 0.08}>
                  <article className="liquid-glass landing-card group h-full rounded-2xl p-6 transition-shadow hover:shadow-md">
                    <div className="mb-4 flex size-11 items-center justify-center rounded-xl bg-primary/10 text-primary transition-transform group-hover:scale-105">
                      <item.icon className="size-5" />
                    </div>
                    <h3 className="font-heading text-xl">{item.title}</h3>
                    <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                      {item.description}
                    </p>
                  </article>
                </Reveal>
              ))}
            </div>
          </div>
        </section>

        {/* Data sources */}
        <section id="datos" className="py-20 md:py-28">
          <div className="mx-auto max-w-6xl px-5 md:px-8">
            <div className="grid items-center gap-12 md:grid-cols-2">
              <Reveal>
                <p className="text-xs font-medium tracking-widest text-primary uppercase">
                  Fuentes
                </p>
                <h2 className="mt-3 font-heading text-3xl tracking-tight md:text-4xl">
                  datos.gov.co en el núcleo del modelo
                </h2>
                <p className="mt-4 text-muted-foreground">
                  Cinco conjuntos abiertos integrados con limpieza, transformación y validación
                  territorial DIVIPOLA antes del entrenamiento.
                </p>
              </Reveal>

              <Reveal delay={0.1}>
                <ul className="space-y-3">
                  {DATASETS.map((name, index) => (
                    <motion.li
                      key={name}
                      initial={reduceMotion ? false : { opacity: 0, x: 16 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true }}
                      transition={{ delay: index * 0.07, duration: 0.4 }}
                      className="liquid-glass-subtle flex items-center gap-3 rounded-xl px-4 py-3 text-sm"
                    >
                      <span className="font-mono text-xs text-primary">{String(index + 1).padStart(2, "0")}</span>
                      {name}
                    </motion.li>
                  ))}
                </ul>
              </Reveal>
            </div>
          </div>
        </section>

        {/* Method */}
        <section id="metodo" className="border-t border-border/40 bg-muted/30 py-20 md:py-28">
          <div className="mx-auto max-w-6xl px-5 md:px-8">
            <Reveal className="mb-14 max-w-2xl">
              <p className="text-xs font-medium tracking-widest text-primary uppercase">
                Método
              </p>
              <h2 className="mt-3 font-heading text-3xl tracking-tight md:text-4xl">
                CRISP-ML con validación temporal
              </h2>
            </Reveal>

            <div className="grid gap-6 md:grid-cols-3">
              {STEPS.map((item, index) => (
                <Reveal key={item.step} delay={index * 0.1}>
                  <article className="liquid-glass-subtle relative h-full rounded-2xl p-6">
                    <span className="font-mono text-xs text-muted-foreground">{item.step}</span>
                    <h3 className="mt-3 font-heading text-xl">{item.title}</h3>
                    <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{item.body}</p>
                  </article>
                </Reveal>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="py-20 md:py-28">
          <Reveal className="mx-auto max-w-3xl px-5 text-center md:px-8">
            <div className="liquid-glass landing-cta rounded-3xl px-6 py-12 md:px-12 md:py-16">
              <ShieldCheck className="mx-auto size-10 text-primary" />
              <h2 className="mt-5 font-heading text-3xl tracking-tight md:text-4xl">
                Apoyo analítico, no decisión automática
              </h2>
              <p className="mx-auto mt-4 max-w-lg text-muted-foreground">
                Cada alerta requiere revisión humana. La plataforma prioriza transparencia,
                trazabilidad y explicabilidad para equipos de vigilancia epidemiológica.
              </p>
              <div className="mt-8 flex flex-wrap justify-center gap-3">
                <Button render={<Link href="/radar" />} size="lg" className="gap-2">
                  Explorar ciudades piloto
                  <ArrowRight className="size-4" />
                </Button>
                <Button render={<Link href="/mapa" />} variant="outline" size="lg">
                  Ver mapa de señales
                </Button>
              </div>
              <p className="mt-8 text-xs text-muted-foreground">
                Equipo ID 200 · Salud y Bienestar · Concurso Datos Abiertos Colombia 2026
              </p>
            </div>
          </Reveal>
        </section>
      </main>

      <footer className="border-t border-border/40 py-8">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-5 text-xs text-muted-foreground md:flex-row md:px-8">
          <p>Plataforma de Inteligencia Epidemiológica Territorial</p>
          <p>Licencia MIT · Datos: datos.gov.co</p>
        </div>
      </footer>
    </div>
  );
}
