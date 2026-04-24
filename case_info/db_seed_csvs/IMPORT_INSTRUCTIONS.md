# Import Order (respect FK dependencies)
1. clinics.csv
2. boxes.csv
3. products.csv
4. doctors.csv      (FK → clinics)
5. patients.csv     (FK → doctors, clinics)
6. jobs.csv         (FK → doctors, patients, boxes, clinics)
7. job_products.csv (FK → products, jobs)
8. job_pictures.csv (FK → jobs)
9. invoices.csv     (FK → jobs)
10. payments.csv    (FK → invoices)
