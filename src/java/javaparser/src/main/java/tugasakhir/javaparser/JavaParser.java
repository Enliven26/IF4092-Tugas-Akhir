package tugasakhir.javaparser;

import com.github.javaparser.*;
import com.github.javaparser.ast.*;
import com.github.javaparser.ast.body.*;
import com.google.gson.Gson;
import java.util.List;
import java.util.ArrayList;
import java.nio.file.Files;
import java.nio.file.Path;

public class JavaParser {
    public static void main(String[] args) {
        if (args.length < 2) {
            throw new IllegalArgumentException("Usage: JavaParserExample <JavaSourceCode> <LineRangesJson>");
        }

        String javaSourceCodeFilePath = args[0];
        String lineRangesJson = args[1];

        try {
            String javaSourceCode = Files.readString(Path.of(javaSourceCodeFilePath));
            
            Gson gson = new Gson();
            List<int[]> lineRanges = gson.fromJson(lineRangesJson, new com.google.gson.reflect.TypeToken<List<int[]>>(){}.getType());
            
            CompilationUnit cu = StaticJavaParser.parse(javaSourceCode);
            List<String> result = new ArrayList<>();
            
            for (Node childNode : cu.getChildNodes()) {
                processNode(childNode, lineRanges, javaSourceCode, result);
            }
            
            for (String declaration : result) {
                System.out.print(declaration);
            }
        }
        catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    private static void processNode(Node node, List<int[]> lineRanges, String javaSourceCode, List<String> result) {
        if (!isDeclarationIncluded(node, lineRanges))
        {
            return;
        }
        
        if (node instanceof ClassOrInterfaceDeclaration) {
            String classDeclarationText = reconstructClassWithFilteredBody((ClassOrInterfaceDeclaration) node, lineRanges, javaSourceCode);
            result.add(classDeclarationText);
        } else {
            result.add(node.toString());
        }
    }

    private static String reconstructClassWithFilteredBody(ClassOrInterfaceDeclaration classDecl, List<int[]> lineRanges, String sourceCode) {
        StringBuilder classDeclarationText = new StringBuilder();
        
        classDeclarationText.append(
            String.join(" ", classDecl.getModifiers().stream()
            .map(Object::toString)
            .toArray(String[]::new)));

        if (classDecl.isInterface()) {
            classDeclarationText.append("interface ");
        } else {
            classDeclarationText.append("class ");
        }
    
        classDeclarationText.append(classDecl.getName()).append(" ");
    
        if (!classDecl.getExtendedTypes().isEmpty()) {
            classDeclarationText.append("extends ");
            classDeclarationText.append(String.join(", ", classDecl.getExtendedTypes().stream()
                    .map(Object::toString)
                    .toArray(String[]::new)));
            classDeclarationText.append(" ");
        }
            if (!classDecl.getImplementedTypes().isEmpty()) {
            classDeclarationText.append("implements ");
            classDeclarationText.append(String.join(", ", classDecl.getImplementedTypes().stream()
                    .map(Object::toString)
                    .toArray(String[]::new)));
            classDeclarationText.append(" ");
        }
    
        classDeclarationText.append("{\n");
    
        for (BodyDeclaration<?> bodyDecl : classDecl.getMembers()) {
            if (isDeclarationIncluded(bodyDecl, lineRanges)) {
                classDeclarationText.append(bodyDecl.toString()).append("\n");
            }
        }
    
        classDeclarationText.append("}\n");
    
        return classDeclarationText.toString();
    }

    private static boolean isDeclarationIncluded(Node declaration, List<int[]> lineRanges) {
        int startLine = declaration.getRange().get().begin.line;
        int endLine = declaration.getRange().get().end.line;

        for (int[] range : lineRanges) {
            if (!(startLine > range[1] || endLine < range[0])) {
                return true;
            }
        }
        return false;
    }

    static class Range {
        private int start;
        private int end;

        public Range(int start, int end) {
            this.start = start;
            this.end = end;
        }

        public int getStart() {
            return start;
        }

        public int getEnd() {
            return end;
        }
    }
}