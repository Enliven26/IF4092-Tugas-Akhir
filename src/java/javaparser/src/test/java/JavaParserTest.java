import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;

public class JavaParserTest {

    private String javaSourceCodeFilePath;
    private String lineRangesJson;
    
    @BeforeEach
    public void setUp() {
        javaSourceCodeFilePath = "src/test/resources/JavaSourceCodeExample.java";
        lineRangesJson = "[[161, 163], [130, 130], [49, 50], [17, 19]]";
    }

    @Test
    public void testJavaParser() {
        // Prepare
        ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
        PrintStream printStream = new PrintStream(outputStream);
        System.setOut(printStream);


        String[] args = new String[]{javaSourceCodeFilePath, lineRangesJson};

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