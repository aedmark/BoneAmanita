import libcst as cst
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand
import glob

class RemoveBroadExcepts(VisitorBasedCodemodCommand):
    def leave_Try(self, original_node: cst.Try, updated_node: cst.Try) -> cst.CSTNode:
        new_handlers = []
        for handler in updated_node.handlers:
            if isinstance(handler.type, cst.Name) and handler.type.value == "Exception":
                # Check if it calls record_crash
                body_str = cst.Module([]).code_for_node(handler.body)
                if "record_crash" in body_str:
                    new_handlers.append(handler)
                    continue
                if "raise" in body_str:
                    new_handlers.append(handler)
                    continue
                continue # Skip this broad exception
            new_handlers.append(handler)
        
        if len(new_handlers) == 0 and updated_node.orelse is None and updated_node.finalbody is None:
            return cst.FlattenSentinel(updated_node.body.body)
            
        return updated_node.with_changes(handlers=new_handlers)

if __name__ == "__main__":
    context = CodemodContext()
    transformer = RemoveBroadExcepts(context)
    
    for filename in glob.glob("**/*.py", recursive=True):
        if ".venv" in filename or "strip_broad_excepts" in filename:
            continue
        try:
            with open(filename, "r") as f:
                source = f.read()
            module = cst.parse_module(source)
            new_module = transformer.transform_module(module)
            if new_module.code != source:
                with open(filename, "w") as f:
                    f.write(new_module.code)
                print(f"Updated {filename}")
        except Exception as e:
            print(f"Failed {filename}: {e}")
