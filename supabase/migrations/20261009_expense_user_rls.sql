alter table public.expenses
    add column if not exists user_id uuid references auth.users (id) on delete cascade;

alter table public.expenses enable row level security;

grant select, insert on public.expenses to authenticated;

drop policy if exists "Users can read their own expenses" on public.expenses;
create policy "Users can read their own expenses"
    on public.expenses
    for select
    to authenticated
    using ((select auth.uid()) = user_id);

drop policy if exists "Users can add their own expenses" on public.expenses;
create policy "Users can add their own expenses"
    on public.expenses
    for insert
    to authenticated
    with check ((select auth.uid()) = user_id);