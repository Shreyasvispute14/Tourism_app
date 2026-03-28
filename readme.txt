prerequistes:-
pip install Flask psycopg2-binary

tourism_app/
│── app.py
└── templates/
    ├── login.html
    ├── book.html
    └── success.html
    
    
    A> To view entries in postgres through terminal:
    	1.sudo -U postgres psql
    	2.\c tourismdb
    	3.\d
    	4.\dt
    	5.\dt+
    	6.\d table_name
    	7.SELECT * FROM table_name 
