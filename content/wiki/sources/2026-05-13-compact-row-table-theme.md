---
title: "Compact Row Table Theme — React + Tailwind"
type: source
tags: [react, tailwind, ui-pattern, ant2, waf-settings]
created: 2026-05-13
updated: 2026-05-13
---

# Compact Row Table Theme — React + Tailwind

## Abstract

วันที่ 2026-05-13 ในระหว่าง redesign หน้า WAF Settings ของ [[Ant2-Proxy-Security-Manager]] v2.4.21 ได้พัฒนา pattern สำหรับทำ dense management list ด้วย React + Tailwind CSS โดยมีเป้าหมายให้ row height ~40px รองรับ 1000+ domains ผ่าน pagination, sticky header, lazy load และ accordion expand ([[compact-row-table-theme]])

## Key Takeaways

- **Container split สำหรับ sticky header**: ถ้า sticky child อยู่ใน container ที่มี `overflow:hidden` จะ sticky ไม่ได้ — ต้องแยก header element ออกเป็น `rounded-t-xl` และ body เป็น `rounded-b-xl` แล้วต่อกัน visual
- **`divide-y` บน container ดีกว่า `border-b` ต่อ row**: ไม่มี double border บน row แรก, ลด boilerplate, ใช้ `divide-slate-100` สำหรับ dense list
- **`max-height` transition แทน `height: auto`**: CSS ไม่ support transition บน `height: auto` — ใช้ `maxHeight: open ? '3200px' : '0'` พร้อม `transition: 'max-height 220ms ease-in-out'`
- **`everOpen` lazy render**: gate panel render ด้วย flag ที่ set ครั้งแรกที่เปิด — panel ไม่ถูก unmount เมื่อปิด ทำให้ form state คงอยู่
- **แยก eager vs lazy API calls**: badge ต้องโหลดตอน mount เสมอ, heavy data (ip-rules) lazy load ตอน expand ครั้งแรก — ถ้า gate config ด้วย everOpen badge จะแสดง `—` จนกว่าจะ click
- **Docker image bake pattern**: `Dockerfile` ที่ใช้ `COPY dist` จะ bake dist เข้า image — ต้อง `docker compose build web` ก่อน `up -d` ทุกครั้งที่แก้ frontend

## Notable Quotes

> "CSS transition บน `height: auto` ไม่ทำงาน ต้องใช้ `max-height` แทน ตั้ง max-height สูงพอ (3200px) แล้ว transition ลงมา 0 เมื่อปิด"

> "sticky child อยู่ใน container ที่มี `overflow:hidden` จะ sticky ไม่ได้"

## Gaps / Unanswered Questions

- `max-height: 3200px` ยังไม่ใช่ virtual scroll — ยังไม่ได้ implement react-window/tanstack-virtual สำหรับ 1000+ rows จริงๆ
- Domain column fixed `w-56` อาจตัดบาง domain ที่ยาวมากได้ อาจต้องปรับ responsive

## See Also

- [[compact-row-table-theme]]
- [[Ant2-Proxy-Security-Manager]]
- [[custom-dropdown-portal-pattern]]
- [[ant2-docker-deploy-pattern]]
