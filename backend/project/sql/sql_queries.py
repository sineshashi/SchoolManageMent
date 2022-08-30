auto_handle_created_at = "CREATE FUNCTION auto_handle_created_at() RETURNS TRIGGER AS $$ BEGIN SET time zone 'utc'; NEW.created_at = CURRENT_TIMESTAMP at time zone 'utc'; RETURN NEW; END; $$ LANGUAGE 'plpgsql';"

auto_handle_updated_at = "CREATE FUNCTION auto_handle_updated_at() RETURNS TRIGGER AS $$ BEGIN SET time zone 'utc'; NEW.updated_at = CURRENT_TIMESTAMP at time zone 'utc'; RETURN NEW; END; $$ LANGUAGE 'plpgsql';"

def auto_now_trigger(table_name):
    return f"CREATE TRIGGER auto_now_{table_name} BEFORE INSERT OR UPDATE ON public.{table_name} FOR EACH ROW EXECUTE PROCEDURE auto_handle_updated_at();"

def auto_now_add_trigger(table_name):
    return f"CREATE TRIGGER auto_now_add_{table_name} BEFORE INSERT ON public.{table_name} FOR EACH ROW EXECUTE PROCEDURE auto_handle_created_at();"