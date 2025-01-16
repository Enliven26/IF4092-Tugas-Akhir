import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.PrintStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.stream.Collectors;

public class JavaParserTest {

    private String javaSourceCode;
    private String lineRangesJson;
    
    @BeforeEach
    public void setUp() {
        Path javaFilePath = Paths.get("src/test/resources/JavaSourceCodeExample.java");
        try {
            javaSourceCode = Files.lines(javaFilePath)
                                  .collect(Collectors.joining(System.lineSeparator()));
        } catch (IOException e) {
            javaSourceCode = "";
            e.printStackTrace();
        }

        lineRangesJson = "[[161, 163], [130, 130], [49, 50], [17, 19]]";
    }

    @Test
    public void testJavaParser() {
        // Prepare
        ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
        PrintStream printStream = new PrintStream(outputStream);
        System.setOut(printStream);


        String[] args = new String[]{javaSourceCode, lineRangesJson};

        // Act
        tugasakhir.javaparser.JavaParser.main(args);

        String result = outputStream.toString().trim();

        // Assert
        assertNotNull(result);
        assertTrue(result.contains("package kafka.examples;"));
        assertTrue(result.contains("import org.apache.kafka.clients.consumer.ConsumerConfig;"));
        assertTrue(result.contains("public class JavaSourceCodeExample extends Thread implements ConsumerRebalanceListener {"));
        assertTrue(result.contains("private final String topic;"));
        assertTrue(result.contains("private final String groupId;"));
        assertTrue(result.contains("public KafkaConsumer<Integer, String> createKafkaConsumer() {"));
        assertTrue(result.contains("public void onPartitionsAssigned(Collection<TopicPartition> partitions) {"));
        assertTrue(result.contains("public void onPartitionsLost(Collection<TopicPartition> partitions) {"));
    }

}