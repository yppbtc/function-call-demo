# 1.创建数据库
CREATE DATABASE `test_fc_db`;
use test_fc_db;
show tables;
# 2.创建数据表
-- 部门表
drop table if EXISTS dept;
create table if not EXISTS dept(
	deptno int primary key,  -- 部门编号  主键：唯一，非空
	dname varchar(14), 		 -- 部门名称
	loc varchar(13)			 -- 部门地址
);

-- 员工表
drop table if EXISTS emp;
create table if not EXISTS emp(
	empno int  primary key, 	-- 员工编号
	ename varchar(10), 			-- 员工姓名
	job varchar(9), 			-- 员工工作
	mgr int, 					-- 员工直属领导编号
	hiredate date, 				-- 入职时间
	sal double, 				-- 工资
	comm double, 				-- 奖金
	deptno int  				-- 所在部门
);

-- 插入数据到部门表
insert into dept values	(10,'财务部','纽约');
insert into dept values (20,'市场部','达拉斯');
insert into dept values	(30,'销售部','芝加哥');
insert into dept values	(40,'运营部','波士顿');

-- 插入数据到员工表
insert into emp values(7369,'smith','职员',7566,'1980-12-17',800,null,20);
insert into emp values(7499,'allen','销售员',7698,'1981-02-20',1600,300,30);
insert into emp values(7521,'ward','销售员',7698,'1981-02-22',1250,500,30);
insert into emp values(7566,'jones','经理',7839,'1981-04-02',2975,null,20);
insert into emp values(7654,'martin','销售员',7698,'1981-09-28',1250,1400,30);
insert into emp values(7698,'blake','经理',7839,'1981-05-01',2850,null,30);
insert into emp values(7782,'clark','经理',7839,'1981-06-09',2450,null,10);
insert into emp values(7788,'scott','职员',7566,'1987-07-03',3000,2000,20);
insert into emp values(7839,'king','董事长',null,'1981-11-17',5000,null,10);
insert into emp values(7844,'turners','销售员',7698,'1981-09-08',1500,50,30);
insert into emp values(7876,'adams','职员',7566,'1987-07-13',1100,null,20);
insert into emp values(7900,'james','职员',7698,'1981-12-03',1250,null,30);
insert into emp values(7902,'ford','销售员',7566,'1981-12-03',3000,null,20);
insert into emp values(7934,'miller','职员',7782,'1981-01-23',1300,null,10);

# TODO 查询
# 需求1: 查询所有员工数量
select count(*) from emp;
# 需求2: 查询每个部门的员工数量
select deptno,count(*) from emp group by deptno;
# 需求3: 查询每个部门的中最高工资
select deptno,max(sal) from emp group by deptno;
# 需求4: 查询每个部门中最高工资的员工信息(要求展示部门名)
with t1 as(
    select e.*,d.dname,
       rank() over (partition by e.deptno order by e.sal desc) r1
    from dept d
        join emp e on d.deptno = e.deptno
)
select * from t1 where r1 = 1;












