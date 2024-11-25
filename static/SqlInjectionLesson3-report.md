# SQL Injection Vulnerability Analysis Report

## Analysis Summary
- Total vulnerabilities found: 3
## Vulnerability Details

### SQL Injection vulnerability detected (1 finding)
#### Finding in injectableQuery
- Statement: `interfaceinvoke statement#0.<java.sql.Statement: int executeUpdate(java.lang.String)>(query)`
- Source: query
- Data Flow: Direct usage


### Unsafe SQL statement creation (2 findings)
#### Finding in injectableQuery
- Statement: `statement#0 = interfaceinvoke connection#0.<java.sql.Connection: java.sql.Statement createStatement(int,int)>(1004, 1007)`
- Source: createStatement
- Data Flow: connection#0 = virtualinvoke $stack8.<org.owasp.webgoat.container.LessonDataSource: java.sql.Connection getConnection()>() -> statement#0 = interfaceinvoke connection#0.<java.sql.Connection: java.sql.Statement createStatement(int,int)>(1004, 1007) -> checkStatement#0 = interfaceinvoke connection#0.<java.sql.Connection: java.sql.Statement createStatement(int,int)>(1004, 1007)
- Detailed Path:
  * `connection#0 = virtualinvoke $stack8.<org.owasp.webgoat.container.LessonDataSource: java.sql.Connection getConnection()>()`
  * `statement#0 = interfaceinvoke connection#0.<java.sql.Connection: java.sql.Statement createStatement(int,int)>(1004, 1007)`
  * `checkStatement#0 = interfaceinvoke connection#0.<java.sql.Connection: java.sql.Statement createStatement(int,int)>(1004, 1007)`

#### Finding in injectableQuery
- Statement: `checkStatement#0 = interfaceinvoke connection#0.<java.sql.Connection: java.sql.Statement createStatement(int,int)>(1004, 1007)`
- Source: createStatement
- Data Flow: statement#0 = interfaceinvoke connection#0.<java.sql.Connection: java.sql.Statement createStatement(int,int)>(1004, 1007) -> checkStatement#0 = interfaceinvoke connection#0.<java.sql.Connection: java.sql.Statement createStatement(int,int)>(1004, 1007) -> interfaceinvoke statement#0.<java.sql.Statement: int executeUpdate(java.lang.String)>(query)
- Detailed Path:
  * `statement#0 = interfaceinvoke connection#0.<java.sql.Connection: java.sql.Statement createStatement(int,int)>(1004, 1007)`
  * `checkStatement#0 = interfaceinvoke connection#0.<java.sql.Connection: java.sql.Statement createStatement(int,int)>(1004, 1007)`
  * `interfaceinvoke statement#0.<java.sql.Statement: int executeUpdate(java.lang.String)>(query)`


