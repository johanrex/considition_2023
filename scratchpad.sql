
select count(*) from solutions;

-- --select count(*) from solutions;
-- select * from solutions 
-- where map_name = 'vasteras'
-- order by total_score desc 
-- limit 10;


-- --get the id with the highest total_score
select * from solutions;

-- delete from solutions 
-- where 
--     map_name = 'vasteras'
--     and 
--     id != (
--         select id from solutions 
--         where map_name = 'vasteras'
--         order by total_score desc
--         limit 1
--     )
-- ;

-- (
--     select id from solutions 
--     where map_name = 'vasteras'
--     order by total_score desc
--     limit 1;
-- );
